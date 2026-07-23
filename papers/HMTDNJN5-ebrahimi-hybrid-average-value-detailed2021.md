# Hybrid Average-Value/Detailed Modeling of Line-Commutated AC–DC Converters With Internal Faults For Electromagnetic Transient Simulations

- 作者：Seyyedmilad Ebrahimi；Navid Amiri；Juri Jatskevich
- 出处：IEEE Transactions on Power Systems
- 年份：2021
- DOI：10.1109/tpwrs.2021.3077391
- Zotero key：HMTDNJN5

> 公式、报告数字和关键事实均直接取自源 PDF，并在本卡引用范围内绑定可定位证据；未引用内容未做全篇转换或认证。

## § 1 — 研究问题与重要性

这篇论文处理的是一个很具体的 EMT 仿真矛盾：晶闸管 line-commutated rectifier（LCR，依靠交流电网电压自然换相的整流器）发生阀器件故障或触发信号丢失后，三相对称性被破坏，系统会出现特征与非特征谐波；详细开关模型能够表现这些波形，却依赖精确的换相事件和很小的时间步长。作者要解决的问题是：能否在保留故障后不平衡波形和直流纹波的同时，仍让 EMT 仿真使用数百微秒量级的固定步长。论文以一个六脉波晶闸管整流器中 \(S_1\) 触发信号丢失、\(T_1\) 等效开路为代表场景，并明确把价值指向离线大系统仿真和实时 EMT 仿真器。[pdf:E01](_evidence/E01-p001-abstract-introduction-fig01.png)

物理上，困难不只是“多了一个故障状态”。健康六脉波桥的重复单元只占一个脉波区间；当一只阀不再导通，原来的相位对称性消失，波形要经过完整交流周期才重复，许多原本因对称性抵消的频率分量重新出现。作者因此需要一种既不逐次追踪每个开关边沿、又能记住完整故障周期内部位置的表示。[pdf:E02](_evidence/E02-p002-fig02-eq01-09.png)

## § 2 — 前人工作与不足

论文点名了三条直接相关的路线。第一，针对不平衡 LCC-HVDC 的 dynamic phasor model 能描述系统级不平衡，但为了得到闭式解析式，需要无损变换器、纯感性换相阻抗、电流开关函数的梯形近似以及交流侧电压无谐波等假设；这些假设使它难以忠实覆盖真实故障换相。第二，作者早先的 parametric average-value model（PAVM）已经能处理内部开关故障，并分别计算正、负序的特征与非特征谐波以及交流波形的直流偏置；代价是每个谐波都要做变换，在固定步长 EMT 中计算量很高。第三，健康 LCR 的 hybrid AVM/detailed model 用一次坐标变换即可带回交流谐波，成本较低，但当时只覆盖正常对称运行。[pdf:E01](_evidence/E01-p001-abstract-introduction-fig01.png)

本文不是重新发明平均值模型，而是补上第三条路线的故障运行缺口：把 parametric functions、reconstruction angle 和对应查表状态扩展到故障配置。实验中的 PAVM 只保留到 7 次谐波，而扩展 hybrid model 直接重构故障波形；这解释了为什么它在波形细节和计算成本上都可能优于逐谐波 PAVM，但也意味着优势与预先准备的查表数据覆盖度紧密绑定。[pdf:E03](_evidence/E03-p003-fig03-04-eq10-16.png)

## § 3 — 重建作者的思考路径

可以从故障后的周期变化逆向重建这条思路。已有知识告诉研究者：健康 \(p\) 脉波整流器因相位对称而每 \(2\pi/p\) 重复一次，单阀故障却把重复周期拉长到 \(2\pi\)。因此，继续用健康模型的短周期 reconstruction angle 必然会把不同故障相位折叠成同一位置，无法恢复完整的不平衡波形；若改为逐次开关，则又失去大步长优势。[pdf:E02](_evidence/E02-p002-fig02-eq01-09.png)

下一步自然是保留“平均量决定慢动态、周期内位置决定纹波形状”这一分工：用 firing angle 和一个表征端口负载的量决定平均传能关系，再用完整周期的相位坐标重构谐波和纹波。故障类型本身不必写成复杂解析式，而可选择一组离线生成的 parametric function stacks。这样，实时计算只需坐标变换、查表与代数重构，不必在每个阀换相时精确定位零点。这一段是基于论文公式和实现图的合理推断，不是作者逐字陈述的研发过程。[pdf:E02](_evidence/E02-p002-fig02-eq01-09.png) [pdf:E03](_evidence/E03-p003-fig03-04-eq10-16.png)

## § 4 — 核心 Intuition

故障不会让平均值建模失效，真正失效的是健康状态下过短的周期坐标。作者把故障状态的 reconstruction angle 扩展到完整交流周期，并让预先生成的查表函数同时依赖 firing angle、动态阻抗和该周期内位置，于是可以用慢变量加周期模板重构故障波形。计算时不再追踪每个开关事件，所以能够增大 EMT 时间步长。[pdf:E02](_evidence/E02-p002-fig02-eq01-09.png)

## § 5 — 具体方法与完整 Pipeline

以论文验证的 \(T_1\) 开路为例，完整 pipeline 如下。

1. **输入与状态选择。** 模型接收交流侧电流 \(\mathbf{i}_{abcs}\)、直流电压 \(v_{dc}\) 和 firing angle \(\alpha\)，输出交流侧电压 \(\mathbf{v}_{abcs}\) 与直流电流 \(i_{dc}\)。`Rectifier State` 选择健康或具体故障配置的 lookup-table stack；`AVM/Detailed` 选择直流侧只输出平均量，还是同时重构纹波。[pdf:E03](_evidence/E03-p003-fig03-04-eq10-16.png)
2. **坐标与工作点。** 交流量被变换到随基波正序同步旋转的 \(qd\) 坐标系。模型由端口平均量形成动态阻抗 \(z_d\)，用它代表当前负载工作点；再由基波相角 \(\theta_e\) 和所选健康/故障周期计算 reconstruction angle \(\theta_{rec}\)。[pdf:E01](_evidence/E01-p001-abstract-introduction-fig01.png) [pdf:E02](_evidence/E02-p002-fig02-eq01-09.png)
3. **离线参数化。** 对不同 firing angle、负载范围以及健康/故障配置数值生成 parametric functions。平均传能和相移函数以 \((\alpha,z_d)\) 存入 2-D lookup tables；交流谐波与直流纹波函数以 \((\alpha,z_d,\theta_{rec})\) 存入 3-D lookup tables。论文明确指出，表格采样分辨率越高，重构通常越准，但构表时间和存储尺寸也越大。[pdf:E02](_evidence/E02-p002-fig02-eq01-09.png)
4. **交流侧重构。** 查询 \(w_v^1,\varphi,w_v^q,w_v^d\)，先得到 \(qd\) 电压的平均分量和振荡分量，再相加并逆变换回 \(abc\) 电压。直观上，平均分量给出能量传递的中心轨迹，振荡分量把阀换相留下的周期性纹理叠回去。[pdf:E03](_evidence/E03-p003-fig03-04-eq10-16.png)
5. **直流侧重构。** 查询 \(w_i^1,w_i^{dc}\)，分别得到平均直流电流和纹波。若 `AVM/Detailed=0`，纹波通道被关掉；若设为 1，则两者相加得到详细直流电流。[pdf:E03](_evidence/E03-p003-fig03-04-eq10-16.png)
6. **故障切换。** 当 \(t=2\,\mathrm{s}\) 时 \(S_1\) 丢失、\(T_1\) 开路，模型切到对应故障表，并把 reconstruction period 从健康脉波区间改为完整交流周期；无需把时间步缩小到逐个开关事件的尺度。[pdf:E02](_evidence/E02-p002-fig02-eq01-09.png) [pdf:E03](_evidence/E03-p003-fig03-04-eq10-16.png)

论文没有报告 FPGA 映射、定点位宽、片上存储布局、流水线、并行调度或 FPGA 上的实时步长；实际平台是 MATLAB/Simulink 离线 PC 与 Opal-RT OP5700。因此，本方法对 FPGA 的直接价值只能判断为“查表加代数运算的结构可能适合硬件化”，这属于基于结构的推断，不是论文验证过的结果。[pdf:E04](_evidence/E04-p004-fig05-06-table01-eq17.png)

## § 6 — 核心数学推导（无形式化数学则跳过）

第一层是**重新定义故障状态的平均窗口**。健康 \(p\) 脉波整流器的原型周期和角度为

\[
T_n=\frac{1}{pf_e},\qquad \beta_n=\frac{2\pi}{p},
\]

故障后则改为

\[
T_f=\frac{1}{f_e},\qquad \beta_f=2\pi.
\]

统一的滑动平均写成

\[
\bar{x}(t)=\frac{1}{T}\int_{t-T}^{t}x(\tau)\,d\tau,\qquad
T=\begin{cases}
T_n,&\text{normal}\\
T_f,&\text{faulty}.
\end{cases}
\]

物理含义是：平均窗口必须覆盖真实重复周期；否则本应属于不同相位位置的故障波形会被错误折叠。[pdf:E02](_evidence/E02-p002-fig02-eq01-09.png)

第二层是**把端口关系无量纲化并参数化**。论文用

\[
w_v^1=\frac{\|\bar{\mathbf v}_{qds}^{e}\|}{\bar v_{dc}},\qquad
w_i^1=\frac{\bar i_{dc}}{\|\bar{\mathbf i}_{qds}^{e}\|},
\]

描述平均交流量与平均直流量的幅值比例，用

\[
\varphi=\tan^{-1}\!\left(\frac{\bar v_{ds}^{e}}{\bar v_{qs}^{e}}\right)
-\tan^{-1}\!\left(\frac{\bar i_{ds}^{e}}{\bar i_{qs}^{e}}\right)
\]

描述电压、电流的相位差；交流振荡和直流纹波则由 \(w_v^q,w_v^d,w_i^{dc}\) 表示。工作点坐标定义为

\[
z_d=\frac{\bar v_{dc}}{\|\bar{\mathbf i}_{qds}^{e}\|}.
\]

这里的 \(z_d\) 不是新增电路元件，而是把当前直流电压与交流基波电流幅值压缩成一个便于查表的“动态阻抗”坐标。[pdf:E02](_evidence/E02-p002-fig02-eq01-09.png)

第三层是**保留周期内相位**：

\[
\theta_{rec}=\operatorname{mod}(\theta_e,\beta),\qquad
\beta=\begin{cases}
\beta_n,&\text{normal}\\
\beta_f,&\text{faulty}.
\end{cases}
\]

健康时相位每 \(2\pi/p\) 回卷，故障时每 \(2\pi\) 回卷；Fig. 2 直观显示了两者的差别。这是整篇论文最关键的数学改动，因为它决定查表函数能否区分故障周期内不同阀组合所对应的波形位置。[pdf:E02](_evidence/E02-p002-fig02-eq01-09.png)

最后是**从平均量与纹波恢复端口变量**。令

\[
\delta=\varphi(z_d,\alpha)+\tan^{-1}\!\left(\frac{\bar i_{ds}^{e}}{\bar i_{qs}^{e}}\right),
\]

则交流平均电压由 \(w_v^1\bar v_{dc}\) 按 \(\delta\) 分解到 \(q,d\) 轴，交流振荡电压由 \(w_v^q,w_v^d\) 乘 \(\bar v_{dc}\) 得到，并有

\[
v_{qs}^{e}=\bar v_{qs}^{e}+\tilde v_{qs}^{e},\qquad
v_{ds}^{e}=\bar v_{ds}^{e}+\tilde v_{ds}^{e}.
\]

直流侧则为

\[
\bar i_{dc}=w_i^1(z_d,\alpha)\|\bar{\mathbf i}_{qds}^{e}\|,\qquad
\tilde i_{dc}=w_i^{dc}(z_d,\alpha,\theta_{rec})\|\tilde{\mathbf i}_{qds}^{e}\|,
\]

\[
i_{dc}=\bar i_{dc}+\tilde i_{dc}.
\]

这组式子的工程意义不是求解半导体开关，而是把预先观测到的平均比例、相位关系和周期纹波模板重新组合成端口波形。[pdf:E03](_evidence/E03-p003-fig03-04-eq10-16.png)

## § 7 — 实验设计与结论

**问题 1：故障发生后，hybrid model 能否跟随详细开关模型的暂态和不平衡波形？** 作者在 60 Hz 同步发电机交流系统上连接 \(2.7\,\mathrm{mF}\) 直流电容和 \(5\,\Omega\) 电阻负载，firing angle 设为 \(30^\circ\)；系统先稳态运行，在 \(t=2\,\mathrm{s}\) 丢失 \(S_1\)，使 \(T_1\) 开路，持续仿真到 6 s。比较对象是详细开关、最多含 7 次谐波的 PAVM、hybrid DC AVM 和 hybrid DC Detailed 四种模型。Fig. 4 中，hybrid DC Detailed 的直流纹波以及交流电流与详细开关结果基本重合；DC AVM 与 PAVM 则只给出直流平均量。Fig. 5 中，hybrid 的交流电压与详细开关曲线重合，而 PAVM 因只重构到 7 次谐波出现可见偏差。这里“基本重合”是作者基于展示波形作出的结论，论文没有为 Fig. 4/5 另报逐点误差。[pdf:E03](_evidence/E03-p003-fig03-04-eq10-16.png) [pdf:E04](_evidence/E04-p004-fig05-06-table01-eq17.png)

**问题 2：计算成本是否低于 PAVM 和详细开关模型？** 作者用固定步长 ode3，在 Intel Core i7-4510U 2.00 GHz PC 上离线运行，并在 OP5700 上实时运行。对 6 s 暂态，hybrid DC AVM 在 \(20\,\mu s\) 下离线耗时 4.07 s、OP5700 CPU 占用 9.43%，PAVM 分别为 40.15 s 和 26.08%；在 \(400\,\mu s\) 下，两者分别为 0.31 s/0.49% 与 2.48 s/1.46%。hybrid DC Detailed 在 \(20\,\mu s\) 下离线耗时 4.73 s，低于详细开关的 8.62 s，但实时 CPU 占用 10.41%，高于详细开关的 7.51%；扩大到 \(400\,\mu s\) 后其占用降到 0.57%，而详细开关无法运行。答案是：该工况中 hybrid 明显降低了 PAVM 的成本，并通过大步长降低实时负载，但在同为 \(20\,\mu s\) 时并非所有实时指标都优于详细开关。[pdf:E04](_evidence/E04-p004-fig05-06-table01-eq17.png)

**问题 3：放大步长后的数值误差多大？** 作者定义

\[
\|e_x\|_2=\frac{\|x_{ref}-x\|_2}{\|x_{ref}\|_2},
\]

其中 \(x\) 是不同步长的 hybrid 相 a 电流轨迹，\(x_{ref}\) 是同一 hybrid model 在 \(0.1\,\mu s\) 下的轨迹。报告结果为：\(10\text{–}100\,\mu s\) 时误差约 \(0.01\%\text{–}0.1\%\)，\(200\text{–}400\,\mu s\) 时约 \(1\%\text{–}2\%\)。这验证的是该模型随步长变化的数值收敛性，不是独立于模型结构的绝对波形误差；把这一结果直接解释成对真实变换器的 1%–2% 误差是不成立的。[pdf:E04](_evidence/E04-p004-fig05-06-table01-eq17.png)

实验没有覆盖多阀同时故障、间歇触发故障、短路型器件故障、频率大幅变化、不同换相阻抗、查表范围外负载，也没有报告 lookup-table 的尺寸、采样网格或生成成本。因此结论只能外推到“单个 \(T_1\) 开路、给定系统与所构表范围内的大步长可行性”，不能据此断言任意内部故障都同样准确。

## § 8 — Take-aways

**5 句话：**  
1. 单阀故障破坏六脉波对称性，使重构周期从一个脉波区间扩展到完整交流周期。[pdf:E02](_evidence/E02-p002-fig02-eq01-09.png)  
2. 作者用故障状态对应的 lookup-table stack 和完整周期 reconstruction angle 保存了这种不对称波形结构。[pdf:E02](_evidence/E02-p002-fig02-eq01-09.png)  
3. 平均量负责慢动态，参数化纹波函数负责恢复交流谐波和直流纹波，从而避免逐个处理换相事件。[pdf:E03](_evidence/E03-p003-fig03-04-eq10-16.png)  
4. 在论文的单阀开路工况中，hybrid model 的波形接近详细开关模型，并显著快于最多含 7 次谐波的 PAVM。[pdf:E03](_evidence/E03-p003-fig03-04-eq10-16.png) [pdf:E04](_evidence/E04-p004-fig05-06-table01-eq17.png)  
5. 方法的交换条件是：必须事先知道故障类别并构造足够分辨率、足够覆盖范围的查表数据。

**3 句话：**  
1. 这项工作的核心不是更精细地追踪开关，而是为故障状态选对周期坐标。  
2. 正确周期加上参数化查表，让端口平均量和纹波在大步长下重新组合。[pdf:E02](_evidence/E02-p002-fig02-eq01-09.png) [pdf:E03](_evidence/E03-p003-fig03-04-eq10-16.png)  
3. 论文证明了一个单阀开路案例的效率与数值可行性，但没有证明开放故障集合上的普适可靠性。

**1 句话：**  
用完整故障周期驱动的 parametric lookup tables 代替逐开关事件求解，是这篇论文用大步长重构故障 LCR 波形的关键。[pdf:E02](_evidence/E02-p002-fig02-eq01-09.png)

## § 9 — 最脆弱的假设

最脆弱的假设是：**运行中的真实故障与负载轨迹始终落在一个已知 fault-state stack 及其 \((\alpha,z_d,\theta_{rec})\) 查表覆盖范围内。** 这是方法能否工作的前提，而不只是精度微调。若实际故障是间歇触发丢失、阀的部分导通、多个阀同时故障，或控制器错误选择了 `Rectifier State`，模型会查询错误的周期模板；此时即便时间积分完全稳定，输出也可能稳定地重构错误波形。论文自己承认 2-D/3-D 表的分辨率决定精度，并存在精度与构表时间、尺寸的折中。[pdf:E02](_evidence/E02-p002-fig02-eq01-09.png)

论文对这一假设提供的证据很窄：验证的是一个 \(T_1\) 开路状态、一个 firing angle、一个电容与电阻负载组合，并没有给出 fault-state 识别误差、表外检测、插值误差上界或未见故障测试。[pdf:E03](_evidence/E03-p003-fig03-04-eq10-16.png) 基于这些证据，可以说作者证明了“已建表状态内”的可行性；仍不能确定的是，状态误判或运行点越界时误差会怎样增长。

## § 10 — 最小复现实验

一周内最值得复现的是“单阀开路后，hybrid reconstruction 能否在 \(400\,\mu s\) 下保持可接受的端口误差，同时详细开关模型出现事件处理问题”。

- **数据与模型：** 在 MATLAB/Simulink 中建立一个六脉波晶闸管 LCR、交流源、直流电容和电阻负载。使用论文明确给出的 60 Hz、\(2.7\,\mathrm{mF}\)、\(5\,\Omega\)、\(\alpha=30^\circ\)，在 2 s 时令 \(T_1\) 开路；论文把同步发电机的其余参数指向文献 [5]，因此复现时应公开自选源阻抗，而不要声称完全复现原系统。[pdf:E03](_evidence/E03-p003-fig03-04-eq10-16.png)
- **实现：** 先以详细开关模型在若干 \((\alpha,z_d)\) 点生成健康和 \(T_1\) 开路的 2-D/3-D tables；再实现 Eqs. (8)–(16) 的查表重构。只覆盖故障前后实际经过的窄工作区，避免把一周时间花在大范围构表。[pdf:E02](_evidence/E02-p002-fig02-eq01-09.png) [pdf:E03](_evidence/E03-p003-fig03-04-eq10-16.png)
- **比较：** 用详细开关模型 \(1\,\mu s\) 轨迹作为独立参考，而不是只用 hybrid 自身的 \(0.1\,\mu s\) 轨迹；对 hybrid 依次使用 20、100、200、400 \(\mu s\)，测量故障后 \(v_{dc},i_{dc},i_{as},v_{as}\) 的归一化 2-norm、峰值误差和执行时间。
- **支持标准：** 若 \(400\,\mu s\) 下关键端口轨迹相对详细开关参考的 2-norm 不超过 2%，且执行时间或实时负载明显下降，就支持核心 claim。
- **反驳标准：** 若表内运行点仍出现相位错位、故障瞬间峰值误差很大，或所谓大步长优势依赖未报告的表格调参，则核心 claim 未被复现。论文报告的 1%–2% 仅是 hybrid 对自身小步长参考的结果，不能替代这项独立比较。[pdf:E04](_evidence/E04-p004-fig05-06-table01-eq17.png)

## § 11 — 最强反例设计

最强反例不是把时间步再放大，而是让系统在**错误或未见的 fault-state stack** 上运行。先只用健康和单个 \(T_1\) 永久开路数据构表，然后测试三类被留出的轨迹：\(T_1\) 间歇丢脉冲、\(T_1+T_4\) 同时开路、以及故障期间负载阶跃使 \(z_d\) 越出构表边界。详细开关模型用很小步长作为参考，hybrid 仍使用论文声称可行的 200–400 \(\mu s\) 步长；同时记录端口电压、电流误差以及模型是否能自行识别表外状态。

这个实验能直接区分两种解释：如果 hybrid 的优势来自可推广的端口参数化，误差应随越界程度平滑增长，并可被检测；如果优势主要来自“为测试故障预存了正确波形模板”，那么一旦故障拓扑或导通序列未被建表，误差会发生结构性跳变，即使数值积分依然稳定。论文目前只显示已知 \(T_1\) 开路状态的波形吻合，且把状态选择作为外部输入，因此无法排除后一种解释。[pdf:E03](_evidence/E03-p003-fig03-04-eq10-16.png)

## § 12 — Follow-up Research Idea

**候选研究方向：从“已知故障目录的波形重构”改为“开放故障集合下、带可验证误差边界的端口 surrogate”。** 这是证据约束下的候选判断；本文及其参考文献不足以完成相关工作检索，因此不声称 novelty。

**(a) 未满足需求。** 实时 EMT 不只需要已建表故障下跑得快，还需要在故障类型未知、多个故障叠加或运行点越界时知道当前 surrogate 是否仍可信。论文的固定 `Rectifier State` 和 lookup-table stacks 没有提供这种自知能力。[pdf:E02](_evidence/E02-p002-fig02-eq01-09.png) [pdf:E03](_evidence/E03-p003-fig03-04-eq10-16.png)

**(b) 研究价值。** 目标应从“为更多故障多建几组表”改成“对端口电压、电流误差给出在线上界，并在上界失效前触发局部高保真求解”。对电力系统 EMT 而言，这把计算加速与故障可信度放进同一验收指标，比单独报告 CPU 时间更接近工程可采用条件。

**(c) 可借鉴工具。** 可以借鉴 certified reduced-order modeling 的 residual-based error estimator、hybrid systems 的 mode uncertainty，以及 active learning 的表外采样策略。它们的作用不是替换 LCR 物理模型，而是把“当前查表结果是否可信”变成可计算量。

**(d) 第一个证伪实验。** 用健康和单阀开路数据训练 surrogate 与误差估计器，完全留出双阀故障、间歇丢脉冲和 \(z_d\) 越界轨迹。若估计器在任何留出轨迹上低估真实端口误差，或为保持覆盖率而频繁回退到详细开关、失去实时优势，这个方向即被第一轮实验否定。

**(e) 与本文的实质区别。** 本文假定先选择正确 fault-state stack，再从固定表重构波形；候选方向把“故障状态和模型可信度未知”本身作为研究对象，并要求输出可证伪的误差边界。它改变了问题定义，而不是在现有模型旁边增加一个更大的查表模块。
