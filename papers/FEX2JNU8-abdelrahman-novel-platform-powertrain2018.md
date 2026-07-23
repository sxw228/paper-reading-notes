# A Novel Platform for Powertrain Modeling of Electric Cars With Experimental Validation Using Real-Time Hardware in the Loop (HIL): A Case Study of GM Second Generation Chevrolet Volt

**作者**：Ahmed S. Abdelrahman；Khalil S. Algarny；Mohamed Z. Youssef  
**出处**：IEEE Transactions on Power Electronics，Vol. 33，No. 11，pp. 9762–9771  
**年份**：2018  
**DOI**：10.1109/TPEL.2018.2793818  
**Zotero key**：FEX2JNU8  
**证据说明**：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

**论文直接陈述的研究问题**是：能否建立一个覆盖电驱、功率变换、控制、动力电池与纵向车辆动力学的整车动力总成模型，并把同一控制逻辑放到真实控制器上、把功率回路放到实时 HIL（hardware-in-the-loop，硬件在环）平台上，以 Chevrolet Volt 第二代为案例核对离线 PSIM 与实时执行结果。摘要把贡献概括为三个层次：对各动力总成部件建立含瞬态的数学模型，在 PSIM 中形成系统仿真，再用 Typhoon HIL 做实时验证；控制算法生成 C 代码并下载到 TI 控制器，而 PMSM 与功率电子硬件由 HIL 实时模拟。[pdf:E01]（PDF 物理页 1，Abstract）

作者进一步把目标表述为一个可迁移到其他 HEV/EV 的“generic platform”，并选择结构更复杂、覆盖面更广的 Chevrolet Volt HEV 版本作为案例；其逻辑是：若这一包含双电机、发动机、行星齿轮、动力电池和双向变换器的系统能被统一建模，较简单的纯电版本也应可由同一框架退化得到。[pdf:E02]（PDF 物理页 2，Section I，左栏第 2–3 段）

这个问题重要，不只是因为仿真可以省去一部分样车成本。真正的工程价值在于，电机电磁动态、DC-link 能量平衡、电池状态、机械负载和控制器时序相互耦合；只在各子系统内分别验证，可能无法暴露跨域瞬态问题。作者把 HIL 的价值归结为虚拟化车辆硬件、以较低时间和成本覆盖多种潜在场景，并在开发早期测试控制器。[pdf:E03]（PDF 物理页 2，Fig. 1–2 及 Section I 右栏）**基于证据的推断**是：这项工作的实际价值取决于两个条件同时成立——模型必须足够接近真实车辆，实时平台也必须在数值误差与执行时序上忠实实现该模型；本文主要展示了后者中的“跨平台波形一致”，但没有完整证明前者。

## § 2 — 前人工作与不足

下面是**论文对相关文献的概述，不是本卡对原始文献的独立复核**。作者称，Dyck、Rahman 与 Dufour 的工作 [10] 聚焦 PMSM 推进系统而忽略电池动态；Tremblay、Dessaint 与 Dekkiche 的通用电池模型 [11] 主要以 SOC 作为状态量以避开 algebraic loop；Tribioli 与 Onori [12] 研究 Chevrolet Volt 的能量管理和油耗；Liu 等 [13] 则研究牵引 PMSM 的控制与 HIL。论文据此把既有工作的共同缺口概括为：有的只覆盖电机，有的只覆盖电池或能量管理，有的只验证控制算法，尚未形成同一案例下贯通功率、控制和机械系统的实时闭环。[pdf:E04]（PDF 物理页 2，Section I，左栏下半部）这些文献的题名与出处也列在论文参考文献 [10]–[13] 中。[pdf:E05]（PDF 物理页 10，References [10]–[13]）

论文参考文献中已经存在面向 EV HIL 的 FPGA-based detailed real-time simulation，以及 FPGA-based 电机驱动和 DC–DC 变换器模型 [17]、[18]。[pdf:E05]（PDF 物理页 10，References [17]–[18]）因此，本文较可信的差异并不是“首次使用 HIL 或 FPGA 做电驱实时仿真”，而是把 Chevrolet Volt 的多个子系统、PSIM 控制设计、Typhoon HIL 和 TI DSP 串成一个具体案例。作者还明确声称这是 Typhoon HIL 首次用于 automotive design research；这个“首次”是作者原文主张，本包没有外部材料可独立核验。[pdf:E03]（PDF 物理页 2，Section I 右栏末段）

另一个更具体的工程差异是控制器建模。作者称 PSIM library model 主要基于 steady-state model，而本文按 transient model 调参，以便接入真实控制器并观察部件的实时行为。[pdf:E06]（PDF 物理页 5，Section II-D，左栏）这里的不足也很清楚：论文没有给出与库模型的定量 baseline，没有报告相同工况下稳态模型与瞬态模型的误差差异，因此“瞬态调参更好”在本文中仍主要是设计选择，而不是经消融证明的结论。

## § 3 — 重建作者的思考路径

以下属于**基于论文证据的逆向重建**。

1. 先从工程失败模式出发：车辆动力总成不是电机、变换器、电池和车身动力学的简单拼接，DC-link、电池功率和负载转矩会在瞬态中相互反馈；只验证单个子系统，无法说明整车控制闭环是否可靠。
2. 选择一个足够复杂且有代表性的对象。作者认为 Chevrolet Volt HEV 比纯 EV 更“inclusive”，因为它同时含电机、发电机、发动机和功率分流机构；这使它成为检验通用平台边界的压力案例。[pdf:E02]（PDF 物理页 2，Section I，左栏中部）
3. 为每个物理域选取可实时计算的模型：PMSM 用旋转坐标系状态方程，车辆用纵向受力与功率平衡，电池不用更重的 electrochemical/look-up-table 模型而采用等效电路，DC–DC 用双向半桥，控制器拆成高层功率分配与低层电压/电流控制。[pdf:E07]（PDF 物理页 3，Section II-A，Eq. (1)–(6)）[pdf:E08]（PDF 物理页 3，Section II-A，Eq. (7)–(15)）[pdf:E09]（PDF 物理页 3，Section II-B 开头）
4. 先在 PSIM 中闭合整车模型，确认电流、转速、转矩、SOC 与 DC-bus 的基本动态，再把功率回路映射到 HIL，把控制代码下载到 TI 控制器，通过 ADC/接口信号形成实时闭环。[pdf:E10]（PDF 物理页 5，Fig. 9–11 及 Section II-D）[pdf:E11]（PDF 物理页 7，Fig. 22–24 及 Section IV）
5. 最后以同一组输出波形在 PSIM 和 HIL 之间做对照，把一致性当作模型可实时实现、控制代码与接口正确的证据。[pdf:E12]（PDF 物理页 8，Fig. 29–31 及 Section IV 末段）[pdf:E13]（PDF 物理页 9，Fig. 32–33）

这条路径合理地把“建模正确性”和“实时实现正确性”放进一条流程，但它也埋下了全文最关键的风险：PSIM 与 HIL 很可能共享同一模型结构和参数，所以两者一致并不自动等价于对真实车辆的独立验证。

## § 4 — 核心 Intuition

不要用彼此割裂的稳态模块来验证整车控制器，而要把电机、电池、变换器和车辆负载的瞬态耦合成一台可实时运行的“虚拟车辆”。[pdf:E01]（PDF 物理页 1，Abstract）先用 PSIM 建立可检查的参考实现，再让真实 TI 控制器驱动 Typhoon HIL 中的功率总成模型；若关键波形在两种执行环境中一致，就说明模型至少能被实时、闭环地执行。[pdf:E03]（PDF 物理页 2，Fig. 1–2）[pdf:E11]（PDF 物理页 7，Section IV）但这种一致性首先验证的是“同一模型的跨平台实现”，不是“模型与真实 Chevrolet Volt 的物理一致性”。

## § 5 — 具体方法与完整 Pipeline

**1. 参数与工况输入。** 案例使用 Chevrolet Volt 的电池、电机和车辆参数。Appendix 报告电池质量 183 kg、能量 18.4 kWh、容量 15 Ah，PMSM 为 8 极、额定表中功率 111 kW，车辆 curb weight 为 1607 kg、迎风面积 2.2 m²、风阻系数 0.28、车轮半径 0.367 m 等。[pdf:E14]（PDF 物理页 9，Tables I–III）速度 profile、转矩需求和当前速度进入主车辆控制器，形成 demanded torque。[pdf:E10]（PDF 物理页 5，Fig. 9）

**2. PMSM 电磁与机械模型。** 三相量先经 Clarke/Park 变换进入同步旋转的 dq 坐标系，电机电气部分以磁链为状态；输出电流再逆变换回相量。机械部分以转速和转角为状态，由电磁转矩与负载转矩之差驱动。[pdf:E07]（PDF 物理页 3，Section II-A-1，Eq. (1)–(6)）[pdf:E08]（PDF 物理页 3，Section II-A-2，Eq. (7)–(10)）

**3. 车辆纵向负载。** 车辆模型把牵引力用于克服质量加速、空气阻力、滚阻和坡度阻力，再用车速乘牵引力得到车轮功率需求；这个功率需求向上游控制器施加机械负载。[pdf:E08]（PDF 物理页 3，Section II-A-2-a，Eq. (11)–(15)）

**4. 电池与双向 DC–DC。** 作者为实时计算舍弃更复杂的 look-up-table/electrochemical 路线，采用非线性等效电路与 SOC 积分模型。[pdf:E09]（PDF 物理页 3，Section II-B）在 dual PMSM EV mode 下，双向半桥作为 boost，把电池侧 360 V 提升到 700 V DC-bus；文中给出 0.8 mH 电感和 4.4 A 纹波设计，称纹波低于稳态输出电流的 10%。再生制动时，功率方向反转，电路按 buck 方式把能量送回电池。[pdf:E15]（PDF 物理页 4，Section II-C，Eq. (20)）

**5. 分层控制。** 低层包括 DC-link controller 和 inverter controller：前者在驱动与再生之间调节电池—母线功率，保持 DC-link；后者根据转矩命令产生六个 IGBT 的触发信号。[pdf:E06]（PDF 物理页 5，Fig. 7–8 与 Section II-D-1）高层包括 power divider controller 和 main vehicle controller：前者在电机、发电机、发动机之间分配功率，后者根据车轮功率需求给出电池参考功率、发动机工作点和转矩命令。[pdf:E10]（PDF 物理页 5，Fig. 9–11 与 Section II-D-2）

**6. 离线 PSIM 参考实现。** 整套模型在 PSIM 中组装，输出三相电流、转速、转矩、SOC、电池电压/电流、DC-bus 电压/电容电流和 PWM。[pdf:E16]（PDF 物理页 6，Fig. 12–14 与 Section III）[pdf:E17]（PDF 物理页 6，Fig. 15–17）[pdf:E18]（PDF 物理页 7，Fig. 18–21）

**7. 实时 HIL 实现。** 功率总成回路在 Typhoon HIL402 上运行；控制电路由 PSIM 生成代码，经 Code Composer Studio 转为 C 并下载至 TI TMS320F28335 控制器，HIL 与控制器通过物理接口/ADC 信号闭环，示波器读取实时波形。[pdf:E03]（PDF 物理页 2，Fig. 1–2）[pdf:E11]（PDF 物理页 7，Fig. 22–24）[pdf:E19]（PDF 物理页 8，Section IV 左栏末段）

**一个具体运行例子。** 在 dual PMSM 驱动工况下，速度 profile 产生转矩需求；电池放电，经双向 DC–DC 升压并维持 DC-link，逆变器驱动 PMSM，车辆模型把空气阻力、滚阻、坡度和加速需求转成负载转矩；主控制器根据反馈持续修正。PSIM 中电池电流为负、SOC 下降，作者据此解释能量从电池流向逆变器和电机。[pdf:E17]（PDF 物理页 6，Fig. 16–17 及正文）[pdf:E18]（PDF 物理页 7，Fig. 18–21）

**EMT/FPGA 实现信息边界。** 论文展示了开关脉冲和实时硬件接口，但没有报告固定步长、开关事件离散方法、multi-rate 划分、代数环处理、数值积分器、定点/浮点精度、延迟预算、deadline miss、FPGA/DSP 资源占用或具体 FPGA mapping。因而可以理解系统级 pipeline，却不能从论文单独重建其确定性实时执行细节。

## § 6 — 核心数学推导（无形式化数学则跳过）

本文有形式化模型，但不是定理式推导；它把已有部件方程组织成可仿真的状态模型。核心数学链条如下。

**PMSM 磁链状态。** 论文在 dq 坐标系中写成

\[
\frac{d}{dt}
\begin{bmatrix}\lambda_{ds}\\ \lambda_{qs}\end{bmatrix}
=
\begin{bmatrix}-R_s/L_d & \omega_r\\-\omega_r & -R_s/L_q\end{bmatrix}
\begin{bmatrix}\lambda_{ds}\\ \lambda_{qs}\end{bmatrix}
+
\begin{bmatrix}1&0&R_s/L_d\\0&1&0\end{bmatrix}
\begin{bmatrix}V_{ds}\\V_{qs}\\\lambda_{PM}\end{bmatrix}.
\]

直觉上，电阻项使磁链衰减，转速耦合项让 d、q 轴相互交换，端电压和永磁体磁链提供驱动。论文随后用 Eq. (2) 从磁链恢复 dq 电流，并用 Eq. (3)–(7) 在三相、αβ 与 dq 坐标之间变换。[pdf:E07]（PDF 物理页 3，Eq. (1)–(6)）[pdf:E08]（PDF 物理页 3，Eq. (7)）需要注意，Eq. (2) 印刷矩阵的第二行含一个直接乘到 \(V_{qs}\) 的“1”，从量纲上看可疑；论文没有解释这一项，本卡不擅自改写。

**机械转矩与车辆负载。** 原文给出

\[
\frac{d\omega_m}{dt}=\frac{1}{2J_m}(T_e-T_L),\qquad
\frac{d\theta_m}{dt}=\omega_m,
\]
\[
T_e=\frac{3}{2}p(\lambda_{ds}i_{qs}-\lambda_{qs}i_{ds}).
\]

这里，转矩差决定加速度，磁链与正交电流的叉乘结构产生电磁转矩；式中的 \(1/(2J_m)\) 按论文原式保留，未见额外推导说明。[pdf:E08]（PDF 物理页 3，Eq. (8)–(10)）

纵向车辆动力学为

\[
m_Ca_C=F_T-(F_{dr}+F_R+m_Cg\sin\delta),
\]
\[
P_d=V_CF_T=V_C(m_Ca_C+F_{dr}+F_R+m_Cg\sin\delta),
\]
\[
a_C=\frac{v(t+\Delta t)-v(t)}{\Delta t},\quad
F_{dr}=\frac{1}{2}\rho V_C^2A_fC_{dr},\quad
F_R=m_Cg\cos(\delta)C_r.
\]

这组式子把驾驶工况转成电驱必须提供的瞬时功率：加速项随质量线性增长，空气阻力随速度平方增长，滚阻与法向载荷近似成正比。[pdf:E08]（PDF 物理页 3，Eq. (11)–(15)）

**电池状态。** 论文对放电与充电分别给出

\[
E=E_o-k\frac{Q}{Q-i_t}-Ae^{-B i_t},
\]
\[
E=E_o-k\frac{Q}{-0.1Q+i_t}-k\frac{Q}{Q-i_t}-Ae^{-B i_t},
\]

并用

\[
i_t=\int_0^t i_{batt}\,dt,\qquad
SOC=SOC(0)-\frac{1}{C_b}\int_0^t i_b\,dt
\]

累计放电量和 SOC。工程直觉是：开路电压随已抽取电荷进入极化区和指数区而变化，SOC 则是电流的库仑积分。[pdf:E20]（PDF 物理页 4，Eq. (16)–(19) 与 Fig. 6）论文同时承认该等效电路没有完整考虑内部电阻随状态变化，换取较低实时计算复杂度。[pdf:E21]（PDF 物理页 4，Section II-B 左栏）

**DC–DC 电感纹波。** 文中用

\[
\Delta I_L=\frac{V_{in}}{V_{out}}\frac{V_{out}-V_{in}}{L f_{sw}}
\]

选择电感。增大 \(L\) 或开关频率 \(f_{sw}\) 会降低纹波；输入/输出电压比决定 boost 工况下的占空与纹波尺度。[pdf:E15]（PDF 物理页 4，Eq. (20)）

## § 7 — 实验设计与结论

**问题 1：离线整车模型是否产生作者预期的动态？ → 实验：** 在 PSIM 中运行整车 schematic，观察三相电流、速度、转矩、SOC、电池电压/电流、DC-bus 与 PWM。**答案：** 三相电流在放大图中接近正弦；转速最终约 2014 r/min，平均转矩约 54 N·m；SOC 在 5 s 窗口内下降，电池电流为负，DC-bus 稳定到约 700 V 附近。[pdf:E16]（PDF 物理页 6，Fig. 12–14 及 Section III 正文）[pdf:E17]（PDF 物理页 6，Fig. 15–17）[pdf:E18]（PDF 物理页 7，Fig. 18–21）这些结果证明模型内部闭环能运行，但“波形合理”不等于与真实车辆相符。

**问题 2：同一控制架构能否在实时 HIL + 实际 TI 控制器上闭环？ → 实验：** 功率回路放在 HIL，控制代码下载到 TMS320F28335，通过接口采集示波器结果。**答案：** 论文报告三相电流 38 A、电池电压 379 V、DC-bus 电压 630 V、平均转矩 57 N·m、PMSM 转速 2010 r/min，并展示 PWM 脉冲。[pdf:E19]（PDF 物理页 8，Fig. 25–28）[pdf:E12]（PDF 物理页 8，Fig. 29–31）这支持“代码生成、I/O 接口和实时闭环可工作”的 claim。

**问题 3：PSIM 与 HIL 是否一致？ → 实验：** 对电机转矩和论文称为 engine speed 的信号叠加比较。**答案：** Fig. 32 的两条稳态转矩曲线高度重合，Fig. 33 的速度曲线在初始振荡后接近；作者据此称两者“very close agreement”。[pdf:E13]（PDF 物理页 9，Fig. 32–33 与 Section V）不过，论文没有给出 RMSE、最大误差、相位误差、置信区间、实时步长、超时次数或多工况统计；Fig. 33 的 caption 还重复写成 motor torque comparison，而纵轴标为 Engine Speed，表明图文编辑存在不一致。

**结论能覆盖到哪里。** 证据足以说明：该模型能在 PSIM 中运行，控制代码能与 Typhoon HIL 形成实时闭环，若干稳态信号在两种执行环境中接近。证据不足以说明：模型已被真实 Chevrolet Volt、真实电池包、真实电机台架或独立测量数据验证；也不足以支持“适用于任何 EV/HEV、列车或飞机”的普适外推。作者在结论中确实提出这种广泛扩展主张，但没有相应跨车型、跨模式或跨物理平台实验。[pdf:E13]（PDF 物理页 9，Section V）

## § 8 — Take-aways

**5 句话**

1. 论文把 PMSM、电池、双向 DC–DC、车辆纵向动力学和分层控制组合成 Chevrolet Volt 动力总成模型，并在 PSIM 中闭环运行。[pdf:E07]（PDF 物理页 3，Section II-A）[pdf:E10]（PDF 物理页 5，Fig. 9–11）
2. 它把功率总成放入 Typhoon HIL，把控制 C 代码下载到 TI 控制器，完成了实际控制硬件参与的实时闭环。[pdf:E11]（PDF 物理页 7，Fig. 22–24）[pdf:E19]（PDF 物理页 8，Section IV）
3. PSIM 报告约 2014 r/min、54 N·m，HIL 报告约 2010 r/min、57 N·m，波形对照显示稳态结果接近。[pdf:E16]（PDF 物理页 6，Section III）[pdf:E12]（PDF 物理页 8，Fig. 29–30）[pdf:E13]（PDF 物理页 9，Fig. 32–33）
4. 论文最可靠的贡献是系统集成与实时可执行性展示，而不是对真实车辆物理精度的独立证明。
5. 缺少物理 ground truth、定量误差指标、实时执行预算和一致参数集，使“generic platform”与“one shirt fits all”的结论明显强于现有证据。[pdf:E21]（PDF 物理页 4，电池描述与 Fig. 5）[pdf:E14]（PDF 物理页 9，Table I）[pdf:E13]（PDF 物理页 9，Section V）

**3 句话**

1. 这是一套把多域动力总成模型从 PSIM 搬到 HIL、并由真实 DSP 控制器闭环驱动的工程流程。[pdf:E03]（PDF 物理页 2，Fig. 1–2）
2. PSIM 与 HIL 的稳态信号接近，说明跨平台实现基本一致，但不能排除两者共享同一错误模型。[pdf:E13]（PDF 物理页 9，Fig. 32–33）
3. 要把它升级为可信的车辆 digital twin，还需要独立实车/台架数据、参数可追溯性、误差统计与实时计算细节。

**1 句话**

本文证明了一个 Chevrolet Volt 多域模型可以在 PSIM 与 Typhoon HIL + TI DSP 闭环中给出相近波形，但尚未证明该模型对真实车辆具有同等精度或对其他动力总成具有普适性。

## § 9 — 最脆弱的假设

**最脆弱的假设是：PSIM 与 HIL 的一致性可以充当模型物理真实性的独立验证。** 如果这一假设不成立，论文的核心贡献就从“经实验验证的通用动力总成模型”缩减为“同一数学模型在两个执行环境中的实现一致性演示”。

这个假设在实际中很容易失效。PSIM schematic、HIL power circuit 和控制代码来自同一建模链条，可能共享相同的结构简化、参数错误、单位错误和控制器调参；只要两个平台忠实实现同一个错误模型，波形仍会高度重合。论文的比较图正是 PSIM 与 HIL 之间的内部对照，没有第三方物理 ground truth，也没有把模型预测与真实 Chevrolet Volt 的电机、电池或车轮数据对齐。[pdf:E11]（PDF 物理页 7，Section IV）[pdf:E13]（PDF 物理页 9，Fig. 32–33）

参数一致性进一步削弱了这一假设。正文称电池包含 197 个 pouch cell、96 串、3 并，而 Fig. 5 caption 写“288 cells”；96×3 也确实等于 288，不等于 197。[pdf:E21]（PDF 物理页 4，Section II-B 与 Fig. 5）Appendix Table I 又列出 192 cells。[pdf:E14]（PDF 物理页 9，Table I）这些互相冲突的数字可能只是排版错误，但论文没有给出可追溯参数表或模型文件，读者无法判断 HIL 实际使用了哪组值。类似地，Eq. (2) 的印刷矩阵存在量纲疑点，完整 PMSM 参数 \(R_s,L_d,L_q,\lambda_{PM},J_m\)、控制器增益、开关频率和实时步长也未报告。

论文为该假设提供的证据是若干波形对照和接近的稳态读数；缺失的证据则是独立物理测量、跨工况误差分布、参数不确定性分析，以及对共享模型错误的隔离测试。由于失败代价是把“实现一致”误判成“物理正确”，这是全文最关键而非次要的局限。

## § 10 — 最小复现实验

一周内最有价值的最小复现，不是重建完整 Chevrolet Volt，而是做一个**独立实现一致性 + 可复现性审计**，直接检验论文能否从公开方程和参数得到其核心稳态结果。

**数据。** 只使用论文 Tables I–III 的电池、电机与车辆参数，Eq. (11)–(20) 的车辆、电池和 DC–DC 方程，以及图中明确报告的目标读数：PSIM 的 2014 r/min、54 N·m，HIL 的 2010 r/min、57 N·m、379 V battery、630 V DC-bus 和 38 A line current。[pdf:E08]（PDF 物理页 3，Eq. (11)–(15)）[pdf:E20]（PDF 物理页 4，Eq. (16)–(19)）[pdf:E15]（PDF 物理页 4，Eq. (20)）[pdf:E16]（PDF 物理页 6，Section III）[pdf:E19]（PDF 物理页 8，Fig. 26–28）[pdf:E12]（PDF 物理页 8，Fig. 29–30）[pdf:E14]（PDF 物理页 9，Tables I–III）

**实现。** 第 1 天建立参数审计表，逐项记录正文、caption 和 Appendix 的冲突；第 2–4 天在一个独立固定步长求解器中实现纵向车辆、SOC 和 DC–DC 子模型，并用一个显式标注为 surrogate 的闭环电机转矩源替代无法复现的 PMSM 部分；第 5 天用第二个求解器或 PSIM 重做同一工况；第 6–7 天比较波形、做步长敏感性和参数扰动。完整 PMSM 无法按论文精确重建，因为 \(R_s,L_d,L_q,\lambda_{PM},J_m\)、控制器增益和 \(f_{sw}\) 等关键量未完整给出；这不是让复现者自行猜值的许可，而是复现结论的一部分。

**测量。** 至少记录稳态速度/转矩、电池端电压、DC-bus、电流、SOC 斜率、最大超调、settling time、两求解器之间的 NRMSE，以及固定步长扫描时的数值稳定性。对电池 cell count 分别采用 192、197 和 288 三种解释，观察能量、等效电压/容量和 SOC 变化是否会改变作者报告的工况。

**预注册判据（候选，不是论文原标准）。** 若两种独立实现能在不拟合图形的前提下得到一致的能量流方向，且关键稳态量相对论文读数偏差不超过 5%、步长缩小后结果收敛，则支持“公开模型至少具备部分可复现性”；若必须猜测关键参数、不同 cell count 解释导致结论改变，或两个求解器不能收敛到同一结果，则反驳“论文材料足以支撑通用、可复现模型”的较强 claim。这个实验不会验证真实 Chevrolet Volt，但会快速判断本文最基本的数学与参数闭环是否成立。

## § 11 — 最强反例设计

最强反例不是再挑一个普通 drive cycle，而是构造一个**共享模型仍会互相吻合、但真实物理系统会系统性偏离**的场景。

具体做法是在独立电池/电机台架或真实车辆记录上，选择低 SOC、低温或高温、大功率脉冲、再生制动切换以及发动机/双电机模式切换组成的工况；这些条件会放大电池内阻变化、开路电压迟滞、热效应、磁饱和、逆变器死区、机械离合/齿轮切换和延迟。本文的电池模型明确为了实时性省略了更复杂的状态依赖，并把内阻变化忽略；正文展示的详细结果主要是单一 dual PMSM 稳态附近的波形。[pdf:E09]（PDF 物理页 3，Section II-B）[pdf:E21]（PDF 物理页 4，Section II-B）[pdf:E16]（PDF 物理页 6，Section III）

实验同时运行三条链：真实台架/车辆、PSIM、HIL。输入保持相同，比较电池端电压、DC-bus、相电流、轴转矩、转速、能量守恒残差和模式切换时刻；先锁定所有参数，禁止用测试数据重新调参。如果 PSIM 与 HIL 仍高度重合，而二者在低 SOC/温度变化或模式切换时同时偏离真实数据，就直接证明“PSIM–HIL agreement”只是共享模型的一致性，不能支撑物理验证。若误差只在切换和极端状态出现，还能定位这套平台的适用域，而不是泛泛地说“模型不够复杂”。

这一反例也能排除替代解释：若作者把误差归因于示波器缩放、接口噪声或单个平台实现，PSIM 与 HIL 同方向偏离真实数据的结果会表明根因在共同模型结构或参数，而非 HIL 硬件本身。

## § 12 — Follow-up Research Idea

**领域判断。** 对 power electronics、motor drives 与 real-time HIL 研究，高影响工作通常需要同时证明模型 fidelity、控制/硬件可实现性、确定性实时执行和对真实系统的独立价值；只增加更多 schematic 或把同一模型搬到更快平台，通常不足以解决本文暴露的验证闭环问题。

**候选研究方向：面向“独立可证伪”的不确定性校准动力总成 digital twin。** 本包禁止外部检索，因此这里不声称 novelty。研究目标从“PSIM 与 HIL 波形一致”改写为：“在未见过的物理工况与模式切换上，实时模型能否给出带置信边界的预测，并同时满足硬实时预算？”模型输出不再只是单条电压/转矩曲线，而是预测区间、参数后验、残差归因和 deadline 证明。

**(a) 未满足需求。** 工程团队需要知道模型在什么 SOC、温度、负载、模式和步长下可信，而不是只知道它能在一个演示工况中实时运行。本文的内部参数冲突、缺失执行细节和共享模型验证说明，当前流程不能回答“何时不可信”。[pdf:E21]（PDF 物理页 4，电池参数描述）[pdf:E14]（PDF 物理页 9，Tables I–III）

**(b) 可能产生的研究价值。** 这会把 HIL 从代码/接口验证工具提升为模型风险管理工具：对每个预测同时报告物理误差预算和计算时序预算，并允许测试工程师据此选择能安全外推的工况。

**(c) 可借鉴的相邻方法。** 可结合 system identification 的可辨识性分析、uncertainty quantification 的校准区间、hybrid systems 的模式切换建模，以及 real-time scheduling/FPGA design 中的 worst-case execution time 分析。对 EMT 实现，可把快速开关子系统与慢速热/电化学子系统做显式 multi-rate 分解，但必须让跨速率接口误差进入总不确定性，而不是只追求更小步长。

**(d) 第一个证伪实验。** 只用一个温度和一个驱动模式的数据辨识模型，然后在未参与拟合的低 SOC、不同温度、再生切换和双电机/发动机模式切换上盲测；预先规定预测区间覆盖率、NRMSE、能量残差和零 deadline miss。如果模型区间不能覆盖真实测量，或为了满足实时预算而产生不可接受的系统性偏差，该方向即被证伪。

**(e) 与本文的实质区别。** 本文的目标是搭建通用模型并用 PSIM–HIL 一致性证明可行；候选方向要求独立物理 ground truth、对模型结构和参数不确定性显式建模、对未见工况做盲测，并把实时执行误差与物理建模误差放在同一验收合同中。它改变的是“验证成功”的定义，而不是简单增加一个电池模块、更换车型或升级 HIL 硬件。
