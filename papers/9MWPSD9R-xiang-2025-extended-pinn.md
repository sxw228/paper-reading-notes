# Extended Physics-Informed Neural Networks for Parameter Identification of Switched Mode Power Converters With Undetermined Topological Durations

- 作者：Yangxiao Xiang；Hongjian Lin；Henry Shu-Hung Chung
- 出处：IEEE Transactions on Power Electronics，Vol. 40，No. 1，pp. 2235–2247
- 年份：2025
- DOI：10.1109/TPEL.2024.3481158
- Zotero key：9MWPSD9R
- 证据说明：公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

论文研究的是：当 switched mode power converter 的某些拓扑持续时间及拓扑切换边界状态无法直接观测时，能否不增加高频采样或零电流检测硬件，仍高精度识别电感、电容、寄生参数、负载、输入电压和二极管正向特性。作者用 discontinuous conduction mode（DCM）buck converter 作为基本案例：一个开关周期依次经历主开关导通 \(T_O\)、二极管续流 \(T_C\) 和电感电流为零后的 \(T_D\)，但在现有低频观测下，\(T_C\) 结束时刻以及该处的输出电压不可见。[pdf:E01]

这不是单纯缺少一个标签。参数识别模型需要知道每段拓扑的起点、终点和持续时间；边界一旦未知，参数误差和边界误差可能互相补偿。传统方案通过 zero-current detector 或远高于开关频率的密集采样补足边界信息，但会增加成本、体积、安全风险和实现难度；低频线性近似则牺牲参数精度。论文因此把问题重写为“同时识别物理参数与隐含拓扑边界”的 hybrid-system inverse problem。[pdf:E02]

价值在于 noninvasive condition monitoring：如果只用控制器本来就能获得的主开关 ON/OFF 时刻处 \(i_L,v_o\)，便能估计老化相关参数，就不必为监测目的改动功率回路或加高速传感链。论文直接声称所提 e-PINN 能在不中断正常运行的前提下完成这种识别；但这项价值目前只在 DCM buck 上验证，尚不能外推为所有 switched converter 的通用能力。[pdf:E01]

## § 2 — 前人工作与不足

论文把相关路线分成三类。

第一类直接恢复缺失边界。zero-current detector 能测出二极管停止导通时刻并触发边界采样，但要增加电路；另一组方法在每个开关周期内密集采样二极管状态、\(i_L\) 或 \(v_o\)，文中概括其采样频率约为开关频率的数百倍，相关实例约 10 MHz。其问题不是理论上不能识别，而是硬件代价会随着 converter switching frequency 上升而更难承受。[pdf:E02]

第二类降低采样频率。Yao 等用多点采样和 least squares 识别 \(C,R_C\)，但仍需每周期采样五次；Qiu 等用 DCM 线性化模型把采样降到控制频率，却因模型简化显著降低精度。论文在同一模拟数据上复算：M1 的 \(C,R_C\) 误差分别为 8% 和 0.3%，采样 100 kHz；M2 虽只采样 20 kHz，但 \(C,R_C,R,V_F\) 误差分别为 17%、67%、60%、147%。[pdf:E10]

第三类是 conventional PINN。PINN 能把动态方程作为训练约束并以较少物理信息反演参数，但标准 piecewise PINN 仍要求每段拓扑的起止状态和持续时间。论文构造的 M3 只能使用可见的 \(T_O\) 段：在同一 Dataset1 上，M3 的 \(L,C,R_C,R,V_{in}\) 误差为 1.2%、5.3%、1.1%、2.4%、0.4%，而 \(V_F\) 无法识别。由此可见，关键缺口不是“有没有 neural network”，而是如何让不可观测边界参与受物理约束的联合训练。[pdf:E09] [pdf:E10]

## § 3 — 重建作者的思考路径

以下是基于论文背景和方法结构的重建，不是作者逐字陈述。

1. 参数识别对状态轨迹敏感，而 switched converter 的轨迹由分段拓扑组成；只要每段边界已知，便可对每段动力学分别约束参数。
2. DCM 的二极管关断边界由参数、开关频率和负载共同决定，不能从 duty cycle 直接得到；这使“未知参数”和“未知边界”形成耦合。
3. 增加 detector 或高速采样能打破耦合，却违背低硬件成本目标；粗线性化能绕开边界，却把误差写进模型。
4. 因而把 \(T_C\) 和边界电压 \(v_{o,C}\) 当作 latent variables，让一个网络从可见端点生成候选 pseudolabel，再让三段拓扑的物理方程判断这些候选是否能共同解释观测。
5. 纯粹无监督的 pseudolabel 很容易落入不可能的局部最优，于是先用 DCM 先验给它加动态可行域：\(0<T_C<T-T_O\)，且关断过程中 \(v_{o,C}\) 必须位于相邻可见电压之间。[pdf:E05]
6. 最终，latent boundary 帮助 piecewise PINNs 使用 \(T_C,T_D\) 两段数据识别参数；piecewise PINNs 的物理残差又反过来训练 pseudolabel network。这就是论文所称的 mutual promotion。[pdf:E10]

## § 4 — 核心 Intuition

不要先“猜参数再补边界”，而是把缺失的拓扑边界当作可学习的隐变量，与系统参数一起求解。pseudolabel generation network 提出满足粗物理边界的 \(T_C,v_{o,C}\)，三段共享权重的 PINNs 再用各自的 converter equations 检查它们能否共同还原可观测端点。只有边界和参数彼此一致时，联合 loss 才能下降。[pdf:E03] [pdf:E05]

## § 5 — 具体方法与完整 Pipeline

以一个 DCM buck switching cycle \(l\) 为例，完整 pipeline 如下。

1. **采集可见端点。** 每周期只使用主开关导通开始、关断时及下一周期开始处的 \(i_L,v_o\)，再加 \(T_O\) 和周期 \(T\)。原始 data slice 是 8-D vector：\([i_{L,I}(l),v_{o,I}(l),i_{L,II}(l),v_{o,II}(l),i_{L,I}(l+1),v_{o,I}(l+1),T_O(l),T]\)。[pdf:E05]
2. **生成隐含边界。** ANN_PLG 接收前六个状态和归一化的 \(T_O/T\)，输出二极管续流时长 \(T_C(l)\) 与二极管关断时的 \(v_{o,C}(l)\)。因为 DCM 关断边界满足 \(i_{L,C}=0\)，无需再由网络估计该电流。[pdf:E05]
3. **施加动态可行域。** dynamic sigmoid-based output constraint 把 \(T_C\) 限在 \(0\) 到 \(T-T_O\) 之间，并把 \(v_{o,C}\) 限在 \(v_{o,I}(l+1)\) 与 \(v_{o,II}(l)\) 之间；随后令 \(T_D=T-T_O-T_C\)。这一步只排除明显违反 DCM 物理的解，并不证明剩余解唯一。[pdf:E05]
4. **分段物理反演。** 三个并行 PINNs 分别处理 \(T_O,T_C,T_D\)。它们的 data-driven 部分共享 weights/biases，各自的 physics-driven 部分采用相应拓扑的 implicit Runge–Kutta 离散模型。latent intermediate states 经物理层映射回每段可见或伪标注的起止状态。[pdf:E03] [pdf:E06]
5. **联合更新。** Loss1 对应完全可见的 \(T_O\) 段；Loss2、Loss3 分别约束含 pseudolabel 的 \(T_C,T_D\) 段。梯度下降同时更新 ANN_PLG、ANN_PINN 和物理层中的待识别参数。论文实际报告的六项性能指标为 \(L,C,R_C,R,V_{in},V_F\)；其中二极管 \(V_F-i_L\) 曲线由 \(\alpha,\beta\) 两个系数表示，\(R_L,R_{dson}\) 则固定为已知值。[pdf:E06] [pdf:E07]
6. **输出。** 网络给出六项参数估计，同时给出每周期的 \(T_C,v_{o,C}\)，因而把原本不可见的拓扑持续时间和边界状态作为联合识别结果。[pdf:E09]

## § 6 — 核心数学推导（无形式化数学则跳过）

论文从一般动态系统开始：

\[
u_t+\mathcal N[u;\lambda]=0 .
\]

对一个区间 \([t_k,t_{k+1}]\) 使用 \(q\)-stage implicit Runge–Kutta，latent stage \(u(k+c_i)\) 同时满足前向与后向关系：

\[
u_i(k)=u(k+c_i)+\Delta t\sum_{j=1}^{q}a_{ij}\mathcal N[u(k+c_j);\lambda],
\]

\[
u_i(k+1)=u(k+c_i)+\Delta t\sum_{j=1}^{q}(a_{ij}-b_j)\mathcal N[u(k+c_j);\lambda].
\]

给定 Butcher tableau 后，\(a_{ij},b_j,c_j\) 固定；可训练物理参数 \(\lambda\) 随同 ANN 权重一起调整，使由 latent stages 推回的区间端点匹配观测。直观上，网络不需要逐时刻还原完整轨迹，而是学习一组“能通过数值积分同时解释两端”的中间状态。[pdf:E03] [pdf:E04]

对 DCM buck，论文用 \(S_w\) 表示主开关状态，用 \(S_c\) 表示电感仍导通的拓扑。二极管正向特性写成

\[
V_F=\beta\log(i_L/\alpha+1),
\]

并与 \(L,C,R_C,R,V_{in}\) 一同进入分段 state-space equations。三个拓扑只需改变 \(S_w,S_c\) 和区间长度，就可由同一组物理参数描述；这正是共享 ANN 表征、分开 physics layer 的依据。[pdf:E04] [pdf:E05]

论文的关键扩展是把 ANN_PLG 的无约束输出经动态 sigmoid 映射为

\[
\widehat v_{o,C}
=v_{o,I}(l+1)
+\frac{v_{o,II}(l)-v_{o,I}(l+1)}{1+\exp(-z_v)},
\qquad
\widehat T_C
=\frac{T-T_O(l)}{1+\exp(-z_T)} ,
\]

其中 \(z_v,z_T\) 是为解释方便引入的 raw network outputs。这样可保证 \(\widehat v_{o,C}\) 和 \(\widehat T_C\) 落在 DCM 先验区间内；但 sigmoid 约束提供的是可行性，不是参数与边界的全局 identifiability 证明。[pdf:E05]

总损失为

\[
\mathrm{Loss}
=\mathrm{Loss}_1+\mu_1\mathrm{Loss}_2+\mu_2\mathrm{Loss}_3,
\]

三项分别比较三个拓扑端点的预测状态与真标签/伪标签。论文取 \(\mu_1=\mu_2=10\)，因为含 pseudolabel 的 Loss2、Loss3 通常小于完全观测的 Loss1；implicit RK stage 数取 \(q=20\)，该设置在 Table V 上得到 0.75% 的系统参数平均误差，优于 \(q=2,5,10,50\) 的 1.73%、1.45%、1.08%、1.36%。[pdf:E06] [pdf:E08]

参数相对误差采用

\[
\mathrm{Error}(\%)=
\frac{\lvert R^{est}-R^{true}\rvert}{R^{true}}\times100\% ,
\]

\(L,C,R_C,V_{in}\) 同理。对 \(V_F\)，作者在 \(i_F=0.2\text{ A}\) 到 \(1.6\text{ A}\) 的 15 个均匀点上比较整条拟合曲线，而不是直接平均 \(\alpha,\beta\) 的相对误差；这是因为工业上更关心 \(V_F-i_F\) 特性，而且曲线对这两个系数并不分别敏感。[pdf:E06] [pdf:E07]

## § 7 — 实验设计与结论

**问题 1：在理想模拟条件下，e-PINN 能否同时识别参数和缺失边界？**  
作者在 MATLAB DCM buck simulation 上构造三个 transient datasets：负载 \(202\Omega\to101\Omega\)（1200 slices）、\(50.5\Omega\to101\Omega\)（1100 slices）以及输出参考 \(18\text{ V}\to24\text{ V}\)（1000 slices），均按 8:2 划分 training/validation。switching frequency 为 20 kHz；训练使用 GeForce RTX 2080Ti。ANN_PLG 为 4 个宽度 30 的 hidden layers，ANN_PINN 为 5 个宽度 50 的 residual hidden layers，learning rate \(5\times10^{-5}\)。[pdf:E06] [pdf:E07]

答案是：六项指标的平均误差在三个 simulation datasets 上分别为 0.75%、0.98%、1.0%。其中 \(L,C,R_C,R,V_{in}\) 均不超过 0.5%，主要较大误差来自 \(V_F\) 的 2.6%、4.4%、4.6%。隐含边界的 MAE 为：\(T_C\) 约 \(0.11\)–\(0.21\,\mu s\)，\(v_{o,C}\) 约 \(0.16\)–\(0.23\,mV\)。[pdf:E08] [pdf:E09]

**问题 2：相较既有低采样方案和 conventional PINN，增益来自哪里？**  
同一 Dataset1 上，e-PINN 在 20 kHz 采样下把六项平均误差做到 0.75%；M2 和 M3 同为 20 kHz，前者因线性化在多个参数上出现两位数至 147% 误差，后者平均精度较差且不能识别 \(V_F\)。作者据此认为：使用 \(T_C,T_D\) 段所含的信息，而不是只拟合可见的 \(T_O\) 段，是精度提升的关键。[pdf:E09] [pdf:E10]

**问题 3：量化、噪声和通道不同步会不会破坏识别？**  
作者在 Dataset1 注入 10-bit ADC quantization、以 20 mA/40 mV 为标准差的 current/voltage Gaussian noise，以及 \(0\)–\(2\,\mu s\) 均匀分布的 \(i_L,v_o\) 通道 synchronization error。三种扰动同时存在时，六项平均误差为 6.55%；其中 \(C,R_C,V_F\) 分别达到 16%、7.7%、11.4%。因此论文所称“robust”是平均误差仍有限，并不意味着所有参数仍保持高精度。[pdf:E09] [pdf:E10]

**问题 4：实物 converter 上能否复现？**  
实物平台采用 FGH40N60UFD 开关管、20 kHz switching/control frequency；Agilent 4294A 的器件测量值作为真值，Keysight DSOS104A 10-bit oscilloscope 采集数据，N2873A 测 \(v_o\)，Tektronix TCP202A 测 \(i_L\)。参数训练仍在 RTX 2080Ti 上执行，而不是在 controller MCU 上执行。[pdf:E10]

三个实验 datasets 与 simulation 对应，data slices 分别为 1714、1626、1618；六项平均误差为 3.25%、2.80%、3.62%。Table XI 进一步显示，Dataset1 使用全动态过程 1200 slices 时平均误差 0.75%，仅用 400 个 steady-state slices 时为 4%；相同约 400 slices 下，覆盖更广 operating region 的动态子集通常更好，说明 excitation diversity 是识别质量的重要条件。[pdf:E09] [pdf:E11]

**问题 5：计算量是否支持“online”？**  
论文报告每 epoch 约 78.0 MFLOPs，总存储约 89.0 kB。作者依据约 \(10^6\) epochs 的收敛图和 Raspberry Pi-4B 的标称 13.5 GFLOPS，估算完整识别约 1.6 h，并认为器件参数变化慢，所以可接受。这里的 1.6 h 是算力换算，不是 Raspberry Pi 或 MCU 上的实测 latency；实验也没有证明控制周期内完成参数更新。因此本卡把 “online” 理解为运行期间可采数、无需扰动 converter，而不是 hard-real-time inference。[pdf:E08] [pdf:E12]

**EMT + FPGA 证据边界：**

- FPGA 实现：未报告。
- HIL：未报告。
- 实时仿真：未报告。
- EMT 细节：未报告。论文中的 implicit Runge–Kutta 是 PINN 训练的物理约束，不是已实现的 EMT 网络求解器；固定步长、实时 deadline、数值稳定性、FPGA resource/timing 和多变换器规模化均未给出。[pdf:E03] [pdf:E12]

## § 8 — Take-aways

**5 句话**

1. e-PINN 把不可观测的拓扑持续时间和边界状态从“缺失测量”变成与 converter parameters 联合求解的 latent variables。[pdf:E03]
2. dynamic sigmoid 先排除违反 DCM 边界的 pseudolabel，三段 piecewise PINNs 再用物理方程筛选能共同解释端点观测的解。[pdf:E05]
3. DCM buck simulation 的六项平均误差约 0.75%–1.0%，实物实验约 2.80%–3.62%，表明该方法在已测试工况内有效。[pdf:E09]
4. 噪声联合注入把平均误差提高到 6.55%，而 steady-state-only 数据也明显变差，说明 sensitivity 和 excitation diversity 仍决定可辨识性。[pdf:E10] [pdf:E11]
5. 论文验证的是 GPU 训练的 20 kHz DCM buck 参数识别，不是 FPGA、HIL、实时 EMT 或 converter-family universality。[pdf:E10] [pdf:E12]

**3 句话**

1. 论文的实质贡献是让 latent topology boundary 与 physical parameters 在同一 physics-constrained objective 中相互校正。
2. 单一 DCM buck 上的 simulation 和 hardware results 支持这种联合识别，但不构成全局 identifiability 或跨拓扑通用性证明。
3. 工程上最值得保留的是“无需零电流检测和高速采样”，最需要警惕的是把小时级训练估算称作实时能力。

**1 句话**

e-PINN 用物理约束的 pseudolabel 补上不可见拓扑边界，从而在不增加边界检测硬件的 DCM buck 上实现了较准的联合参数识别，但其 identifiability、实时性和跨拓扑能力仍未闭合。

## § 9 — 最脆弱的假设

最脆弱的假设是：仅凭主开关 ON/OFF 处的 \(i_L,v_o\) 和自然运行中的 transient data，系统参数与 latent \(T_C,v_{o,C}\) 在所关注范围内足够可辨识，即低 loss 的可行解不会有多组物理上不同却观测等价的组合。

这项假设一旦失败，核心贡献会直接失效：dynamic sigmoid 只保证 \(T_C,v_{o,C}\) 落在边界内，无法阻止 \(L,C,R_C,R,V_{in},\alpha,\beta\) 与 topology duration 彼此补偿。论文已经出现了这一风险的局部迹象：\(V_F\) 对动态过程敏感度较低，所以其误差明显高于其他参数；\(R_L,R_{dson}\) 因在 DCM 小电流下敏感度太低而被排除，不参与识别。[pdf:E08] [pdf:E09]

作者提供的支持主要是经验性的：三种 transient processes、三组实物数据、扰动注入，以及不同 data coverage 的 downsampling 实验。尤其 Table XI 表明，1200 个覆盖动态过程的 slices 平均误差为 0.75%，而 400 个 steady-state slices 为 4%，说明 excitation richness 确实影响结果。[pdf:E11] 但论文没有给出 structural identifiability、局部 Hessian/Fisher information、multi-start 解分布或跨 topology 的验证。因此“六项参数与两个隐变量可唯一分离”仍是只在当前 buck 和当前工况附近获得支持的假设，不是已证明事实。

## § 10 — 最小复现实验

一周内最值得复现的不是完整实物平台，而是“pseudolabel + 全三拓扑物理约束是否真的优于只用 \(T_O\) 的 conventional PINN”。

1. 在 MATLAB 或 Python 建立与 Table I 一致的 20 kHz DCM buck，至少生成 Dataset1：负载 \(202\Omega\to101\Omega\)，1200 switching-cycle slices；只导出每周期的 \(i_{L,I},v_{o,I},i_{L,II},v_{o,II},i_{L,I}(l+1),v_{o,I}(l+1),T_O,T\)。[pdf:E06] [pdf:E07]
2. 实现两个模型：e-PINN 使用 ANN_PLG、dynamic constraints 和三段 PINNs；baseline M3 只使用 \(T_O\) 段。采用论文的 \(q=20\)、ANN_PLG 4×30、ANN_PINN 5×50、\(\mu_1=\mu_2=10\)。[pdf:E07] [pdf:E08]
3. 至少运行五个随机初始化；测量六项参数误差、\(\widehat T_C\) MAE、\(\widehat v_{o,C}\) MAE，并记录不同初始化是否收敛到不同参数组合。论文未报告这种重复性统计，这是复现实验应补的检查。
4. **支持条件：** e-PINN 的多次运行中位平均参数误差接近或低于 1%，\(T_C\) MAE 不高于约 \(0.21\,\mu s\)，\(v_{o,C}\) MAE 不高于约 \(0.23\,mV\)，且持续优于 M3。[pdf:E09]
5. **反驳条件：** 多个初始化得到相近端点 loss 却产生显著不同的参数/边界，或 e-PINN 对 M3 的优势在轻微噪声下消失。前者会直接暴露联合识别的非唯一性，后者会削弱“缺失边界可由物理约束补足”的核心 claim。

## § 11 — 最强反例设计

最强反例不是再增加一种随机噪声，而是构造“观测上几乎等价、内部参数不同”的物理工况。

让 buck 长时间停留在窄 operating region，只保留稳态附近的 ON/OFF endpoint samples；随后通过成对调整 \(L\)、二极管 \(V_F-i_L\) 特性和 \(T_C\)，构造两组都满足 sigmoid 边界、且在观测端点上差异低于 10-bit ADC 分辨率的参数组合。用多起点 e-PINN 同时拟合，检查是否能以相近 loss 稳定收敛到两组不同解。再把这两组模型放到未用于训练的负载阶跃上比较真实轨迹。

如果训练端点无法区分两组解、但未见 transient 上的 \(i_L,v_o\) 明显分叉，那么论文当前实验只能证明“优化器在给定数据上找到了一个好解”，不能证明它识别了真实参数。Table XI 已给出攻击方向：steady-state-only Case 8 的平均误差 4%，明显差于覆盖完整动态过程的 0.75%；Fig. 9 还显示 \(V_F,R_L,R_{dson}\) 存在低敏感度区。[pdf:E09] [pdf:E11] 这个反例比单纯增加噪声更强，因为它直接挑战 latent boundary 与 parameter vector 的 identifiability，而不是只测试数值鲁棒性。

## § 12 — Follow-up Research Idea

在 power electronics 领域，高影响工作通常不仅要给出更低平均误差，还要闭合物理可解释性、跨工况有效性、硬件可实现性和工程代价。基于第 9 节的核心缺口，一个更有价值的候选方向是 **identifiability-aware active e-PINN**：不再被动等待自然 transient，而是联合设计最小安全 excitation、采样窗口和不确定性证书，确保 latent topology duration 与关键 parameters 在采集数据中确实可分离。

**(a) 未满足需求。** 当前方法不知道一次运行数据是否“信息足够”；Table XI 只能事后说明 broad operating coverage 更好，不能在识别前判断这一批数据是否会产生多解。[pdf:E11]

**(b) 研究价值。** 若能在不增加 zero-current detector 的前提下，用幅度受限、对正常控制影响可量化的短暂 excitation 保证参数可辨识，并在结果旁给出 uncertainty/condition number，就会把“得到一个点估计”提升为“知道何时可以信任这个估计”。这比给网络再加一层更接近 condition monitoring 的真实决策需求。

**(c) 可借鉴工具。** 可连接 hybrid-system observability、optimal experimental design、Fisher information、Bayesian system identification 与 safe input design。pseudolabel network 仍处理隐含边界，但训练目标增加信息矩阵或 posterior contraction，而不是只最小化 endpoint residual。

**(d) 第一个证伪实验。** 在相同采样数、ADC 分辨率和允许的 converter output deviation 下，对比自然 transient、随机小扰动与 active excitation；跨多个初值和未见负载测试参数误差、posterior width、多解率和额外能量。如果 active strategy 不能显著降低多解率或未见工况误差，这个方向即被证伪。

**(e) 与本文的实质区别。** 本文固定自然运行数据后联合估计 parameters 与 latent boundaries，并以平均误差评价；候选工作首先决定“采什么数据才能让问题可识别”，其次输出可信度，再做参数估计。它改变了问题定义，而不是只更换 converter 或增加网络模块。

该方向仅由本 PDF 的敏感度、downsampling 和验证边界推导，相关工作未做外部检索，因此是候选研究想法，不声称具有 novelty。FPGA 部署、HIL、实时仿真和 EMT 实现仍未报告；若后续要进入这些方向，必须分别补充 fixed-step solver、latency/WCET、resource usage、数值稳定性和真实 hardware timing 证据。[pdf:E11] [pdf:E12]
